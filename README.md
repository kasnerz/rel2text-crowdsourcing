# rel2text-crowdsourcing

A crowdsourcing app used for gathering data for verbalizing relations in knowledge graphs.

See https://arxiv.org/abs/2210.07373 for more details.

## Quickstart
```
pip install -r requirements.txt

flask --app 'app:build_app(num_rel=20,compl_code="ABC")' run
```