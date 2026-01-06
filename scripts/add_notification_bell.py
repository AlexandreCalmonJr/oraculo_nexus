# Script to add notification bell to base_user.html
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

template_path = r'c:\Users\Administrator\oraculo_nexus\templates\user\base_user.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the notification bell HTML
notification_bell_html = '''
            <!-- Notification Bell -->
            <div class="notification-bell-container">
                <a href="{{ url_for('notifications.notifications_page') }}" class="topbar-btn notification-bell" id="notificationBell" title="Notificacoes">
                    <i class="fas fa-bell"></i>
                    <span class="notification-badge" id="notificationBadge" style="display: none;">0</span>
                </a>
            </div>
'''

# Find and replace - add notification bell after theme toggle
old_text = '''            </button>

            <a href="{{ url_for('user.profile') }}'''

new_text = '''            </button>
''' + notification_bell_html + '''
            <a href="{{ url_for('user.profile') }}'''

# Replace
if old_text in content:
    content = content.replace(old_text, new_text)
    print("SUCCESS: Notification bell added!")
else:
    # Try with different line endings
    old_text_alt = old_text.replace('\n', '\r\n')
    new_text_alt = new_text.replace('\n', '\r\n')
    
    if old_text_alt in content:
        content = content.replace(old_text_alt, new_text_alt)
        print("SUCCESS: Notification bell added (CRLF)!")
    else:
        print("ERROR: Could not find target location")
        sys.exit(1)

# Write back
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated successfully!")
