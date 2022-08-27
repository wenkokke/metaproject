# Metaproject

Scaffold new projects from Jinja2 templates, *e.g., running...

```bash
metaproject init wenkokke/metaproject-haskell \
  --project=my-project \
  --github_username=wenkokke \
  --github_repository=my-project
```

... creates ...

```
test
├── .github
│   ├── workflows
│   │   └── ci.yml
│   └── dependabot.yml
├── dist-newstyle
│   └── cache
├── src
│   └── Test.hs
├── test
│   └── Spec.hs.jinja2
├── .python-version
├── ChangeLog.md
├── README.md
├── bumpver.toml
├── cabal.project
├── hie.yaml
├── pre-commit-config.yaml
├── requirements-dev.txt
└── test.cabal
```