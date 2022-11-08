from markdown2 import Markdown
from jinja2 import Environment, FileSystemLoader

import datetime
import email.utils
import glob
import configparser


md = Markdown(extras=["fenced-code-blocks","metadata","task_list","tables","target-blank-links"])
templates = Environment(loader=FileSystemLoader("templates"))
src_folder = "Output"
out_folder = "docs"
md_files = glob.glob(f"./{src_folder}/*.md")
config = configparser.ConfigParser()
config.read("config.ini")

posts = []

def render_markdown_post(html,metadata=None,template="post.html",posts=[]):
	global templates
	return templates.get_template(template).render(content=html,posts=posts, config=config)

for md_file in md_files:
    with open(md_file) as f:
        _html = md.convert(f.read())
        _post_title = _html[4:_html.find("</h1>")]
        _post = _html.metadata
        _post["title"] = _post_title
        _post["link"] = md_file.replace(f"./{src_folder}","").replace("md","html")
        _post["pdf"] = md_file.replace(f"./{src_folder}","").replace("md","pdf")
        _html.metadata = _post
        print(_html.metadata)
        _html.metadata["description"] = _html.metadata["DESC"]
        _html.metadata["DATE"] = email.utils.format_datetime(datetime.datetime.strptime(_html.metadata["DATE"],"%Y-%m-%d %H:%M")) 
        with open(md_file.replace(src_folder,out_folder).replace("md","html"),"w") as f:
            f.write(render_markdown_post(_html))

        posts.append(_html)

for pdf_file in glob.glob(f"./PDFs/*.pdf"):
    pdfbytes = open(pdf_file,"rb").read()
    with open(pdf_file.replace("PDFs","docs").replace("RENAMED - ",""),"wb") as f:
        f.write(pdfbytes)
with open(f"{out_folder}/index.html","w") as f:
    f.write(render_markdown_post(md.convert(open("index.md").read()),template="index.html",posts=posts))