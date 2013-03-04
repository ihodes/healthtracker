import os 

from app import *

HOST = os.environ.get("HOST_NAME", "healthtracker.herokuapp.com")
## Mailer
def send_status_update_email(user):
    api_endpoint = "https://api.mailgun.net/v2/healthtracker.mailgun.org/messages"
    api_key = "key-25pn6z0fogz-783zc7gcloa8gs23qkq2"
    from_email = "Health Tracker <hello@healthtracker.mailgun.org>"
    to_email = user.email
    email_subject = "Update Your Health Today"

    status_update_links = ["Let us know how you're feeling today. \n\n 0 being the first and worst, 5 being the best."]
    for value in range(6):
        status_update_link = construct_status_update_url(user, value)
        status_update_links.append("{0}: {1}".format(value, status_update_link))

    email_text = "\n\n".join(status_update_links)
    # template = env.get_template('status_update.html')
    # email_text = template.render(val_links=status_update_links)

    return requests.post(api_endpoint,
                         auth=("api", api_key),
                         data={"from": from_email,
                               "to": to_email,
                               "subject": email_subject,
                               "text": email_text})
    

def construct_status_update_url(user, value):
    url_base = "http://{0}/tracker?auth_token={1}&value={2}"
    host = HOST
    auth = user.auth_token
    return url_base.format(host, auth, value)


if __name__ == '__main__':
    for user in User.query.all():
        send_status_update_email(user)
