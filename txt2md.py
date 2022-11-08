def replace_markdown_chars(text):
    text = text.replace("* *","**")
    text = text.replace("[ ", "[")
    text = text.replace(" ]", "]")
    text = text.replace(" .", ".")

    return text

def text2mdtxt(text):
    """Converts text to Markdown text."""
    txt_block = ""
    incomplete_line = ""

    # Check if text has special characters
    ## ;;; denotes that the text contains headers

    has_header = False
    double_trouble = False
    if ";;;" in text:
        has_header = True
        txt_block = "---\n"
        if text.count(";;;") > 1:
            double_trouble = True
        second_time = False
        if double_trouble:
            for line in text.splitlines():
                if ";;;" in line:
                    if second_time:
                        txt_block += "\n---\n"
                        break
                    else:
                        second_time = True
                else:
                    txt_block += line + "\n"
        else:
            for line in text.splitlines():
                if ";;;" in line:
                    txt_block += "---\n"
                    break
                else:
                    txt_block += line + "\n"
                
    second_time = False
    for line in text.splitlines():
        if has_header:
            if double_trouble:
                if ";;;" in line:
                    if second_time:
                        has_header = False
                        continue
                    else:
                        second_time = True
                        has_header = False
                        continue
            else:
                if ";;;" in line:
                    has_header = False
                    continue
                else:
                    continue
        if line[0] == '#': # Header
            txt_block += incomplete_line + "\n"
            incomplete_line = ""
            line = line.replace(' #', '#')
            txt_block += line + "\n"
        elif "&#182;" in line.replace(' ',''):
            txt_block += incomplete_line + "\n\n"
            incomplete_line = ""
        else:
            line = line.strip()
            incomplete_line += line + " "
    txt_block += incomplete_line + "\n"
    return replace_markdown_chars(txt_block)

if __name__ == "__main__":
    with open("./Output/2022-11-08-hello-world.md") as f:
        text = f.read()

    print(text2mdtxt(text))