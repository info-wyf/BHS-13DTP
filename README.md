### BHS13DTP

# Resources
• code: https://github.com/info-wyf/BHS-13DTP

• Examples: https://opentechschool.github.io/python-flask/core/forms.html

• Learning resources: https://www.w3schools.com/html/html_forms.asp

# Tips:
use "pip install -r requirements.txt" to install Flask Flask-SQLAlchemy and Flask-WTF.

# Trouble shooting

1.Problem:
remote: Support for password authentication was removed on August 13, 2021.
remote: Please see https://docs.github.com/get-started/getting-started-with-git/about-remote-repositories#cloning-with-https-urls for information on currently recommended modes of authentication.
fatal: Authentication failed for 'https://github.com/info-wyf/BHS-12DTP.git/'

1.Solutions:
use GitHub CLI or git-credential-manager:
https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git

2.Problem:
sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError) Error binding parameter 2: type 'list' is not supported
[SQL: UPDATE orders SET name=?, extras=?, update_time=? WHERE orders.id = ?]

2.Solutions:
order.extras = ', '.join(form.extras.data)  # Convert list to string to solve the problems above

