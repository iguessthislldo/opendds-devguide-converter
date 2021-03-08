from docutils import nodes

url_base = 'https://github.com'


# Turns :ghfile:`README.md` into the equivalent of ``README.md`` that is a
# link to https://github.com/objectcomputing/OpenDDS/blob/master/README.md
def ghfile(name, rawtext, text, lineno, inliner, options={}, content=[]):
    app = inliner.document.settings.env.app
    repo = app.config.github_link_repo
    commitish = app.config.github_link_commitish
    url = '{}/{}/blob/{}/{}'.format(url_base, repo, commitish, text)
    options['classes'] = ['github_link_literal']
    node = nodes.reference(rawtext, text, refuri=url, **options)
    return ([node], [])


# Turns :ghissue:`213` into the equivalent of:
#   `Issue #213 on GitHub <https://github.com/objectcomputing/OpenDDS/issues/213>`_
def ghissue(name, rawtext, text, lineno, inliner, options={}, content=[]):
    app = inliner.document.settings.env.app
    repo = app.config.github_link_repo
    url = '{}/{}/issues/{}'.format(url_base, repo, text)
    text = 'Issue #{} on GitHub'.format(text)
    node = nodes.reference(rawtext, text, refuri=url, **options)
    return ([node], [])


# Can turn :ghpr:`1` into the equivalent of:
#   `Pull Request #1 on GitHub <https://github.com/objectcomputing/OpenDDS/pull/1>`_
def ghpr(name, rawtext, text, lineno, inliner, options={}, content=[]):
    app = inliner.document.settings.env.app
    repo = app.config.github_link_repo
    url = '{}/{}/pull/{}'.format(url_base, repo, text)
    text = 'Pull Request #{} on GitHub'.format(text)
    node = nodes.reference(rawtext, text, refuri=url, **options)
    return ([node], [])


def setup(app):
    app.add_config_value('github_link_repo', None, 'env', types=[str])
    app.add_config_value('github_link_commitish', None, 'env', types=[str])

    app.add_role('ghfile', ghfile)
    app.add_role('ghissue', ghissue)
    app.add_role('ghpr', ghpr)
