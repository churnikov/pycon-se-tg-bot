# Bot for PyCon Sweden conference

## Development

For local set up, change docker image to `pycon_se_bot` in `docker-compose.yml` and run:

```bash
$ cp .env.example .env
# add your telegram token to .env from @BotFather
$ docker build -t pycon_se_bot .
$ docker-compose up 
```


