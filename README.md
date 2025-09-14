# repo-name-generator
Aineopintojen harjoitustyö: Algoritmit ja tekoäly 2025


python -m pytest tests/test_trie.py -v

pytest tests

pytest --cov=src --cov-branch --cov-report=term-missing
- prints a text table in the terminal and lists missing line numbers (“term-missing”).

pytest --cov=src --cov-branch --cov-report=html
- generates an HTML report in the htmlcov/ folder (open htmlcov/index.html in a browser)

pytest --cov=src --cov-branch --cov-report=term-missing --cov-report=html
- both

start .\htmlcov\index.html  

---

git status --ignored -s