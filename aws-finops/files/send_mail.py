def send_email(from_address, to_address, deleted_resources, skip_delete_resources, notify_resources, check_resources):
    subject = "AWS: Auto clean resource data"
    verified = verify_email_identity(from_address)

    if verified:
        html_body = get_email_body(deleted_resources, skip_delete_resources, notify_resources, check_resources)
        send_html_email(from_address, to_address, subject, html_body)
        print("Email sent successfully")
    else:
        print("Warning: Email address is not verified yet, unable to send email notification.")
