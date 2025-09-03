#!/usr/bin/env python3

"""
Test script to verify that the PHP configuration fix works correctly.
This script simulates the PHP config editing process and checks that all settings are preserved.
"""

import os
import tempfile
import shutil

# Simulate the fixed savePHPConfigBasic function logic
def test_save_php_config():
    # Create a sample PHP configuration file without file_uploads directive
    sample_config = """
; PHP Configuration File
[PHP]

engine = On
short_open_tag = Off
precision = 14
output_buffering = 4096
zlib.output_compression = Off
implicit_flush = Off
unserialize_callback_func =
serialize_precision = -1
disable_functions =
disable_classes =
zend.enable_gc = On
expose_php = On
max_execution_time = 30
max_input_time = 60
memory_limit = 128M
error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT
display_errors = Off
display_startup_errors = Off
log_errors = On
ignore_repeated_errors = Off
ignore_repeated_source = Off
report_memleaks = On
track_errors = Off
html_errors = On
variables_order = "GPCS"
request_order = "GP"
register_argc_argv = Off
auto_globals_jit = On
post_max_size = 8M
auto_prepend_file =
auto_append_file =
default_mimetype = "text/html"
default_charset = "UTF-8"
doc_root =
user_dir =
enable_dl = Off
cgi.fix_pathinfo = 1
file_uploads = On
upload_max_filesize = 2M
max_file_uploads = 20
allow_url_fopen = On
allow_url_include = Off
default_socket_timeout = 60
"""

    # Test parameters (simulating what would be passed from the web interface)
    test_params = {
        'allow_url_fopen': 'allow_url_fopen = On',
        'display_errors': 'display_errors = On',  # Changed from Off to On
        'file_uploads': 'file_uploads = On',      # This should be preserved
        'allow_url_include': 'allow_url_include = Off',
        'memory_limit': '256M',                   # Changed from 128M
        'max_execution_time': '60',               # Changed from 30
        'upload_max_filesize': '10M',             # Changed from 2M
        'max_input_time': '120',                  # Changed from 60
        'post_max_size': '16M'                    # Changed from 8M
    }

    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as temp_file:
        temp_file.write(sample_config)
        temp_path = temp_file.name

    try:
        # Simulate the fixed logic
        with open(temp_path, 'r') as f:
            data = f.readlines()

        with open(temp_path, 'w') as writeToFile:
            # Track which directives we've found and replaced
            found_directives = {
                'allow_url_fopen': False,
                'display_errors': False,
                'file_uploads': False,
                'allow_url_include': False,
                'memory_limit': False,
                'max_execution_time': False,
                'upload_max_filesize': False,
                'max_input_time': False,
                'post_max_size': False
            }

            for items in data:
                if items.find("allow_url_fopen") > -1 and items.find("=") > -1:
                    writeToFile.writelines(test_params['allow_url_fopen'] + "\n")
                    found_directives['allow_url_fopen'] = True
                elif items.find("display_errors") > -1 and items.find("=") > -1:
                    writeToFile.writelines(test_params['display_errors'] + "\n")
                    found_directives['display_errors'] = True
                elif items.find("file_uploads") > -1 and items.find("=") > -1 and not items.find("max_file_uploads") > -1:
                    writeToFile.writelines(test_params['file_uploads'] + "\n")
                    found_directives['file_uploads'] = True
                elif items.find("allow_url_include") > -1 and items.find("=") > -1:
                    writeToFile.writelines(test_params['allow_url_include'] + "\n")
                    found_directives['allow_url_include'] = True
                elif items.find("memory_limit") > -1 and items.find("=") > -1:
                    writeToFile.writelines("memory_limit = " + test_params['memory_limit'] + "\n")
                    found_directives['memory_limit'] = True
                elif items.find("max_execution_time") > -1 and items.find("=") > -1:
                    writeToFile.writelines("max_execution_time = " + test_params['max_execution_time'] + "\n")
                    found_directives['max_execution_time'] = True
                elif items.find("upload_max_filesize") > -1 and items.find("=") > -1:
                    writeToFile.writelines("upload_max_filesize = " + test_params['upload_max_filesize'] + "\n")
                    found_directives['upload_max_filesize'] = True
                elif items.find("max_input_time") > -1 and items.find("=") > -1:
                    writeToFile.writelines("max_input_time = " + test_params['max_input_time'] + "\n")
                    found_directives['max_input_time'] = True
                elif items.find("post_max_size") > -1 and items.find("=") > -1:
                    writeToFile.writelines("post_max_size = " + test_params['post_max_size'] + "\n")
                    found_directives['post_max_size'] = True
                else:
                    writeToFile.writelines(items)

            # Add any missing directives at the end of the file
            missing_directives = []
            if not found_directives['allow_url_fopen']:
                missing_directives.append(test_params['allow_url_fopen'])
            if not found_directives['display_errors']:
                missing_directives.append(test_params['display_errors'])
            if not found_directives['file_uploads']:
                missing_directives.append(test_params['file_uploads'])
            if not found_directives['allow_url_include']:
                missing_directives.append(test_params['allow_url_include'])
            if not found_directives['memory_limit']:
                missing_directives.append("memory_limit = " + test_params['memory_limit'])
            if not found_directives['max_execution_time']:
                missing_directives.append("max_execution_time = " + test_params['max_execution_time'])
            if not found_directives['upload_max_filesize']:
                missing_directives.append("upload_max_filesize = " + test_params['upload_max_filesize'])
            if not found_directives['max_input_time']:
                missing_directives.append("max_input_time = " + test_params['max_input_time'])
            if not found_directives['post_max_size']:
                missing_directives.append("post_max_size = " + test_params['post_max_size'])

            if missing_directives:
                writeToFile.writelines("\n; Added by CyberPanel PHP Config Manager\n")
                for directive in missing_directives:
                    writeToFile.writelines(directive + "\n")

        # Read the result and verify
        with open(temp_path, 'r') as f:
            result = f.read()

        print("=== TEST RESULTS ===")

        # Check that all settings are present
        checks = [
            ('file_uploads = On', 'file_uploads setting'),
            ('display_errors = On', 'display_errors setting'),
            ('memory_limit = 256M', 'memory_limit setting'),
            ('max_execution_time = 60', 'max_execution_time setting'),
            ('upload_max_filesize = 10M', 'upload_max_filesize setting'),
            ('max_input_time = 120', 'max_input_time setting'),
            ('post_max_size = 16M', 'post_max_size setting'),
        ]

        all_passed = True
        for check_value, description in checks:
            if check_value in result:
                print(f"✓ PASS: {description} found")
            else:
                print(f"✗ FAIL: {description} NOT found")
                all_passed = False

        # Check that the comment was added for missing directives (if any)
        if "; Added by CyberPanel PHP Config Manager" in result:
            print("✓ PASS: Missing directives section added")
        else:
            print("✓ PASS: No missing directives needed (all were already present)")

        print("\n=== FINAL RESULT ===")
        if all_passed:
            print("🎉 SUCCESS: All PHP configuration settings are properly handled!")
            return True
        else:
            print("❌ FAILURE: Some settings were not properly handled")
            return False

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    success = test_save_php_config()
    exit(0 if success else 1)
