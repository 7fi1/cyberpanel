#!/bin/bash

# Test Plugin Installation Script for CyberPanel
# This script installs the test plugin from GitHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PLUGIN_NAME="testPlugin"
PLUGIN_DIR="/home/cyberpanel/plugins"
CYBERPANEL_DIR="/usr/local/CyberCP"
GITHUB_REPO="https://github.com/cyberpanel/testPlugin.git"
TEMP_DIR="/tmp/cyberpanel_plugin_install"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Function to check if CyberPanel is installed
check_cyberpanel() {
    if [ ! -d "$CYBERPANEL_DIR" ]; then
        print_error "CyberPanel is not installed at $CYBERPANEL_DIR"
        exit 1
    fi
    print_success "CyberPanel installation found"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating plugin directories..."
    
    # Create plugins directory if it doesn't exist
    mkdir -p "$PLUGIN_DIR"
    chown -R cyberpanel:cyberpanel "$PLUGIN_DIR"
    chmod 755 "$PLUGIN_DIR"
    
    # Create temp directory
    mkdir -p "$TEMP_DIR"
    
    print_success "Directories created"
}

# Function to download plugin from GitHub
download_plugin() {
    print_status "Downloading plugin from GitHub..."
    
    # Remove existing temp directory
    rm -rf "$TEMP_DIR"
    
    # Clone the repository
    if command -v git &> /dev/null; then
        git clone "$GITHUB_REPO" "$TEMP_DIR"
    else
        print_error "Git is not installed. Please install git first."
        exit 1
    fi
    
    print_success "Plugin downloaded"
}

# Function to install plugin files
install_plugin() {
    print_status "Installing plugin files..."
    
    # Copy plugin files to CyberPanel directory
    cp -r "$TEMP_DIR" "$CYBERPANEL_DIR/$PLUGIN_NAME"
    
    # Set proper permissions
    chown -R cyberpanel:cyberpanel "$CYBERPANEL_DIR/$PLUGIN_NAME"
    chmod -R 755 "$CYBERPANEL_DIR/$PLUGIN_NAME"
    
    # Create symlink in plugins directory
    ln -sf "$CYBERPANEL_DIR/$PLUGIN_NAME" "$PLUGIN_DIR/$PLUGIN_NAME"
    
    print_success "Plugin files installed"
}

# Function to update Django settings
update_django_settings() {
    print_status "Updating Django settings..."
    
    SETTINGS_FILE="$CYBERPANEL_DIR/cyberpanel/settings.py"
    
    if [ -f "$SETTINGS_FILE" ]; then
        # Check if plugin is already in INSTALLED_APPS
        if ! grep -q "testPlugin" "$SETTINGS_FILE"; then
            # Add plugin to INSTALLED_APPS
            sed -i '/^INSTALLED_APPS = \[/a\    "testPlugin",' "$SETTINGS_FILE"
            print_success "Added testPlugin to INSTALLED_APPS"
        else
            print_warning "testPlugin already in INSTALLED_APPS"
        fi
    else
        print_error "Django settings file not found at $SETTINGS_FILE"
        exit 1
    fi
}

# Function to update URL configuration
update_urls() {
    print_status "Updating URL configuration..."
    
    URLS_FILE="$CYBERPANEL_DIR/cyberpanel/urls.py"
    
    if [ -f "$URLS_FILE" ]; then
        # Check if plugin URLs are already included
        if ! grep -q "testPlugin.urls" "$URLS_FILE"; then
            # Add plugin URLs
            sed -i '/^urlpatterns = \[/a\    path("testPlugin/", include("testPlugin.urls")),' "$URLS_FILE"
            print_success "Added testPlugin URLs"
        else
            print_warning "testPlugin URLs already configured"
        fi
    else
        print_error "URLs file not found at $URLS_FILE"
        exit 1
    fi
}

# Function to run Django migrations
run_migrations() {
    print_status "Running Django migrations..."
    
    cd "$CYBERPANEL_DIR"
    
    # Run migrations
    python3 manage.py makemigrations testPlugin
    python3 manage.py migrate testPlugin
    
    print_success "Migrations completed"
}

# Function to collect static files
collect_static() {
    print_status "Collecting static files..."
    
    cd "$CYBERPANEL_DIR"
    python3 manage.py collectstatic --noinput
    
    print_success "Static files collected"
}

# Function to restart CyberPanel services
restart_services() {
    print_status "Restarting CyberPanel services..."
    
    # Restart LiteSpeed
    systemctl restart lscpd
    
    # Restart CyberPanel
    systemctl restart cyberpanel
    
    print_success "Services restarted"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check if plugin files exist
    if [ -d "$CYBERPANEL_DIR/$PLUGIN_NAME" ]; then
        print_success "Plugin directory exists"
    else
        print_error "Plugin directory not found"
        exit 1
    fi
    
    # Check if symlink exists
    if [ -L "$PLUGIN_DIR/$PLUGIN_NAME" ]; then
        print_success "Plugin symlink created"
    else
        print_error "Plugin symlink not found"
        exit 1
    fi
    
    # Check if meta.xml exists
    if [ -f "$CYBERPANEL_DIR/$PLUGIN_NAME/meta.xml" ]; then
        print_success "Plugin metadata found"
    else
        print_error "Plugin metadata not found"
        exit 1
    fi
    
    print_success "Installation verified successfully"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
    print_success "Cleanup completed"
}

# Function to show installation summary
show_summary() {
    echo ""
    echo "=========================================="
    echo "Test Plugin Installation Summary"
    echo "=========================================="
    echo "Plugin Name: $PLUGIN_NAME"
    echo "Installation Directory: $CYBERPANEL_DIR/$PLUGIN_NAME"
    echo "Plugin Directory: $PLUGIN_DIR/$PLUGIN_NAME"
    echo "Access URL: https://your-domain:8090/testPlugin/"
    echo ""
    echo "Features Installed:"
    echo "✓ Enable/Disable Toggle"
    echo "✓ Test Button with Popup Messages"
    echo "✓ Settings Page"
    echo "✓ Activity Logs"
    echo "✓ Inline Integration"
    echo "✓ Complete Documentation"
    echo "✓ Official CyberPanel Guide"
    echo "✓ Advanced Development Guide"
    echo ""
    echo "To uninstall, run: $0 --uninstall"
    echo "=========================================="
}

# Function to uninstall plugin
uninstall_plugin() {
    print_status "Uninstalling testPlugin..."
    
    # Remove plugin files
    rm -rf "$CYBERPANEL_DIR/$PLUGIN_NAME"
    rm -f "$PLUGIN_DIR/$PLUGIN_NAME"
    
    # Remove from Django settings
    SETTINGS_FILE="$CYBERPANEL_DIR/cyberpanel/settings.py"
    if [ -f "$SETTINGS_FILE" ]; then
        sed -i '/testPlugin/d' "$SETTINGS_FILE"
    fi
    
    # Remove from URLs
    URLS_FILE="$CYBERPANEL_DIR/cyberpanel/urls.py"
    if [ -f "$URLS_FILE" ]; then
        sed -i '/testPlugin/d' "$URLS_FILE"
    fi
    
    # Restart services
    restart_services
    
    print_success "Plugin uninstalled successfully"
}

# Main installation function
main() {
    echo "=========================================="
    echo "CyberPanel Test Plugin Installer"
    echo "=========================================="
    echo ""
    
    # Check for uninstall flag
    if [ "$1" = "--uninstall" ]; then
        uninstall_plugin
        exit 0
    fi
    
    # Run installation steps
    check_root
    check_cyberpanel
    create_directories
    download_plugin
    install_plugin
    update_django_settings
    update_urls
    run_migrations
    collect_static
    restart_services
    verify_installation
    cleanup
    show_summary
    
    print_success "Test Plugin installation completed successfully!"
}

# Run main function with all arguments
main "$@"
