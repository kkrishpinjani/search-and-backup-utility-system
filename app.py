from flask import Flask, render_template, request
from database import create_tables
from scanner import scan_directory
from search import search_by_name
from backup import create_backup
from restore import restore_backup
import os

app = Flask(__name__)
create_tables()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    path = request.form["path"]
    scan_directory(path)
    return "Scan Completed ✅ <br><a href='/'>Go Back</a>"


@app.route("/search", methods=["POST"])
def search():
    name = request.form["name"]
    results = search_by_name(name)
    return "Search Completed (Check Terminal Output) <br><a href='/'>Go Back</a>"


@app.route("/backup", methods=["POST"])
def backup():
    path = request.form["path"]
    create_backup(path)
    return "Backup Created ✅ <br><a href='/'>Go Back</a>"


@app.route("/restore", methods=["POST"])
def restore():
    zip_path = request.form["zip_path"]
    restore_location = request.form["restore_location"]
    restore_backup(zip_path, restore_location)
    return "Restore Done ✅ <br><a href='/'>Go Back</a>"


if __name__ == "__main__":
    app.run(debug=True)