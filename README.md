# mail2blog

Mail2blog is a small utility that enables static site blog publishing via email. It fetches email messages from an IMAP server, and converts them into plain text files to be further processed in a site generation pipeline. It features image attachment downloading and conversion. Presently it only works with Jekyll, but should be straightforward to extend to other static blog frameworks.

Copy `.env.example` to `.env` and then update the environment variables.

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
source .env
python main.py
```