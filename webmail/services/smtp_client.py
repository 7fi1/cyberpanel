import smtplib
import ssl


class SMTPClient:
    """Wrapper around smtplib.SMTP for sending mail via Postfix."""

    def __init__(self, email_address, password, host='localhost', port=587):
        self.email_address = email_address
        self.password = password
        self.host = host
        self.port = port

    def send_message(self, mime_message):
        """Send a composed email.message.EmailMessage via SMTP with STARTTLS.

        Returns:
            dict: {success: bool, message_id: str or None, error: str or None}
        """
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            smtp = smtplib.SMTP(self.host, self.port)
            smtp.ehlo()
            smtp.starttls(context=ctx)
            smtp.ehlo()
            smtp.login(self.email_address, self.password)
            smtp.send_message(mime_message)
            smtp.quit()

            message_id = mime_message.get('Message-ID', '')
            return {'success': True, 'message_id': message_id}
        except smtplib.SMTPAuthenticationError as e:
            return {'success': False, 'message_id': None, 'error': 'Authentication failed: %s' % str(e)}
        except smtplib.SMTPRecipientsRefused as e:
            return {'success': False, 'message_id': None, 'error': 'Recipients refused: %s' % str(e)}
        except Exception as e:
            return {'success': False, 'message_id': None, 'error': str(e)}

    def save_to_sent(self, imap_client, raw_message):
        """Append sent message to the Sent folder via IMAP."""
        sent_folders = ['Sent', 'INBOX.Sent', 'Sent Messages', 'Sent Items']
        for folder in sent_folders:
            try:
                if imap_client.append_message(folder, raw_message, '\\Seen'):
                    return True
            except Exception:
                continue
        try:
            imap_client.create_folder('Sent')
            return imap_client.append_message('Sent', raw_message, '\\Seen')
        except Exception:
            return False
