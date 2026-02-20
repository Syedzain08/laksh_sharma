from flask import Flask, render_template, send_from_directory, url_for, Response
from yaml import safe_load
from os import path, getenv
from dotenv import load_dotenv
from flask_frozen import Freezer
from shutil import copy

app = Flask(__name__)
freezer = Freezer(app)

src_config = path.join("static", "admin", "config.yml")
dest_config = path.join("build", "admin", "config.yml")

load_dotenv()
site_url = getenv("SITE_URL")


def load_data(filename):
    load_path = path.join("content", filename)
    with open(load_path, "r") as f:
        return safe_load(f)


@app.context_processor
def inject_settings():
    with open("content/seo.yml", "r") as f:
        seo = safe_load(f)

    return {
        "seo": seo,
    }


@app.route("/")
def index():
    hero = load_data("hero.yml")
    about = load_data("about.yml")
    work_data = load_data("work.yml")
    shows_data = load_data("shows.yml")
    testi_data = load_data("testimonials.yml")
    contact = load_data("contact.yml")

    return render_template(
        "index.html",
        hero=hero,
        about=about,
        work=work_data.get("videos", []),
        work_heading=work_data.get("heading", "MY WORK"),
        shows=shows_data.get("shows", []),
        shows_heading=shows_data.get("heading", "UPCOMING SHOWS"),
        countdown_target=shows_data.get("countdown_target", ""),
        countdown_venue=shows_data.get("countdown_venue", ""),
        testimonials=testi_data.get("testimonials", []),
        testimonials_heading=testi_data.get("heading", "TESTIMONIALS"),
        contact=contact,
    )


@app.route("/admin/")
@app.route("/admin/<path:path>")
def admin(path="index.html"):
    return send_from_directory("static/admin", path)


# -- Robots Route -- #
@app.route("/robots.txt")
def robots_txt():
    lines = [
        "User-agent: *",
        "Disallow:",
        f"Sitemap: {url_for('sitemap', _external=True)}",
    ]
    return Response("\n".join(lines), mimetype="text/plain")


# --- Sitemap Route---- #
@app.route("/sitemap.xml")
def sitemap():
    urls = [
        {"loc": url_for("index", _external=True), "priority": "1.0"},
    ]

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url in urls:
        xml.append("  <url>")
        xml.append(f"    <loc>{url['loc']}</loc>")
        xml.append(f"    <priority>{url['priority']}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")

    return Response("\n".join(xml), mimetype="text/xml")


if __name__ == "__main__":
    with open("static/admin/config.yml", "r") as f:
        config_content = f.read()

    import re

    config_content = re.sub(r"(site_url:\s*).*", f"\\1{site_url}", config_content)
    config_content = re.sub(r"(display_url:\s*).*", f"\\1{site_url}", config_content)
    config_content = re.sub(r"(base_url:\s*).*", f"\\1{site_url}", config_content)

    with open("static/admin/config.yml", "w") as f:
        f.write(config_content)

    app.config["FREEZER_BASE_URL"] = site_url
    freezer.init_app(app)
    freezer.freeze()
    copy(src_config, dest_config)
