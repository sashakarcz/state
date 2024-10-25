name: Create Graphs

on:
  schedule:
    - cron:  */5 * * * *

jobs:
  make-graphs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install plotly pyyaml

      - name: Run checks
        run: |
          python python/plot.py

      - name: Commit changes
        run: |
          git config --global user.name "github-actions"
          git config --global user.email "github-actions@github.com"
          git add .
          git commit -m "Automated commit from GitHub Actions"
          git push
