.. include:: global.rst.inc
.. _installation:

How to contribute
============

Create a github account if you do not already have one.
Fork the project repository: click on the “Fork” button near the top of the qkit git repository page.
This creates a copy of the repository under your account on the github server.
Clone your fork to your computer::

        git clone https://github.com/YOURLOGIN/qkit-gla.git

Create a feature branch to hold your changes::

        git checkout -b my-feature

Navigate to qkit-gla folder and change/add the files you want
The changed added/modified files can be listed using::

        git status

and the changes can be reviewed using::

        git diff

Apply the changes using::

        git add --all

and then ::

        git commit –m “new changes”

To update your github repository with your new commit(s), run::

        git push origin my-feature:my-feature

Finally, when your feature is ready, and all tests pass, go to the github page of your repository fork,
and click “Pull request” to send your changes to the maintainers for review.
