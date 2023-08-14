# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_core.ipynb.

# %% auto 0
__all__ = ['vline_settings', 'hline_settings', 'line_settings', 'text_settings', 'page0_text', 'is_invoice_text', 'is_invoice',
           'is_invoice_chain', 'get_fullest_row', 'num_full_parts', 'get_table_items', 'row_check', 'extract_sub_text',
           'find_target_index', 'json_str', 'str_to_json', 'extract_text', 'extract_order_docs', 'info_order_docs',
           'pdf_to_info_order_docs', 'qa_llm_chain', 'fix_json', 'json_response', 'info_json', 'order_json',
           'pdf_to_info_order_json']

# %% ../nbs/01_core.ipynb 2
from .imports import *
from .utils import *

# %% ../nbs/01_core.ipynb 5
def page0_text(pdf):
    loaded_pdf = PdfReader(pdf)
    p = loaded_pdf.pages[0]
    return p.extract_text()


def is_invoice_text(text, model):
    return model(text).detach().cpu().item() == 0


def is_invoice(pdf, model, device=None):
    if model is None:
        model = load_invoice_model(device=device)
    return is_invoice_text(page0_text(pdf), model)


def is_invoice_chain(
    model,
    device=None,
    input_variables=["pdf"],
    output_variables=["is_invoice"],
    verbose=False,
):
    return transform_chain(
        is_invoice,
        transform_kwargs={"model": model, "device": device},
        vars_kwargs_mapping={input_variables[0]: "pdf"},
        input_variables=input_variables,
        output_variables=output_variables,
        verbose=verbose,
    )


# %% ../nbs/01_core.ipynb 7
vline_settings = {
    "horizontal_strategy": "text",
    "vertical_strategy": "lines",
    "intersection_x_tolerance": 5,
    "snap_y_tolerance": 5,
    "join_x_tolerance": 5,
    "join_y_tolerance": 5,
}
hline_settings = {
    "horizontal_strategy": "lines",
    "vertical_strategy": "text",
    "intersection_x_tolerance": 5,
    "snap_y_tolerance": 5,
    "join_x_tolerance": 5,
    "join_y_tolerance": 5,
}
line_settings = {
    "horizontal_strategy": "lines",
    "vertical_strategy": "lines",
    "intersection_x_tolerance": 5,
    "snap_y_tolerance": 5,
    "join_x_tolerance": 5,
    "join_y_tolerance": 5,
}
text_settings = {
    "horizontal_strategy": "text",
    "vertical_strategy": "text",
    "intersection_x_tolerance": 5,
    "snap_y_tolerance": 5,
    "join_x_tolerance": 5,
    "join_y_tolerance": 5,
}
text_settings = {
    # "intersection_x_tolerance": 5,
    # "snap_y_tolerance": 5,
    # "join_x_tolerance": 5,
    # "join_y_tolerance": 5,
    "text_layout": True
}


def get_fullest_row(table):
    rows = [r for r in table if full_row(r)]
    if len(rows) == 0:
        rows = table
    row = max(rows, key=len)
    return row, table.index(row)


def num_full_parts(row):
    return len([p for p in row if not empty_part(p)])


def get_table_items(table):
    if table is None or len(table) == 0:
        return []

    cols, cols_idx = get_fullest_row(table)
    for i, c in enumerate(cols):
        if empty_part(c):
            cols[i] = f"col_{i}"

    # let's assume that the first full row after the cols row is the first item
    first_order_row_idx = get_first_full_row(table[cols_idx + 1 :])[1]
    if first_order_row_idx is None:
        first_order_row_idx = get_first_non_empty_row(table[cols_idx + 1 :])[1]
    if first_order_row_idx is None:
        first_order_row_idx = 0
    first_order_row_idx += cols_idx + 1

    items = []
    item = {c: "" for c in cols}
    first_order_row_idx = min(first_order_row_idx, len(table) - 1)
    order_table = table[first_order_row_idx:]
    curr_row_len = num_full_parts(order_table[0])
    for row in order_table:
        if ((num_full_parts(row) == curr_row_len) or empty_row(row)) and len(item) > 0:
            items.append(item)
            item = {c: "" for c in cols}
            if not empty_row(row):
                curr_row_len = num_full_parts(row)
        for i, c in enumerate(cols):
            row_part = row[i]
            if not empty_part(row_part):
                row_part = " ".join(row[i].split("\n"))
                item[c] += row_part + " "
    items.append(item)
    return items


# %% ../nbs/01_core.ipynb 8
def row_check(row, target_list, target_thresh=2):
    """
    Checks if the given row contains the target elements.

    Parameters:
        row (str): A string representing the row to check.
        target_list (list): A list of strings representing the target elements.
        target_thresh (int): The minimum number of target elements that must be present in the row.

    Returns:
        bool: True if the row contains the target elements, False otherwise.
    """
    check_list = [hc for hc in target_list if hc.lower() in row.strip().lower()]
    return len(check_list) >= target_thresh


def extract_sub_text(
    text,
    top_cols,
    bottom_cols,
    top_thresh=2,
    bottom_thresh=1,
    alt_top_index=0,
    alt_bottom_index=0,
):
    """
    Extracts the text between the top_cols and bottom_cols.
    """
    top_idx = find_target_index(
        text, top_cols, target_thresh=top_thresh, alt_index=alt_top_index
    )
    bottom_idx = find_target_index(
        text[::-1], bottom_cols, target_thresh=bottom_thresh, alt_index=alt_bottom_index
    )
    bottom_idx = len(text) - bottom_idx
    return (
        [t for t in text[top_idx : bottom_idx + 1] if len(t.strip()) > 0],
        top_idx,
        bottom_idx,
    )


def find_target_index(data, target_list, target_thresh=2, alt_index=0):
    """
    Finds the index of the row in the given data that contains the target elements.

    Parameters:
        data (list): A list of strings representing the data.
        target_list (list): A list of strings representing the target elements.
        target_thresh (int): The minimum number of target elements that must be present in a row.

    Returns:
        int: The index of the row that contains the target elements. If no such row exists, returns alt_index.
    """
    target_idx = None
    for idx, row in enumerate(data):
        if row_check(row, target_list, target_thresh):
            target_idx = idx
            break
    if target_idx is None:
        msg.warn(f"No target found in data. Setting it to {alt_index}.", spaced=True)
        target_idx = alt_index
    return target_idx


# %% ../nbs/01_core.ipynb 9
def json_str(x):
    x = x[x.find("{") : x.rfind("}") + 1]
    x = x.splitlines()
    jstr = [x[0]]
    for s in x[1:]:
        if ":" not in s and s.strip() != "}":
            jstr[-1] = jstr[-1][:-2] + " " + s[1:]
        else:
            jstr.append(s)
    jstr = " ".join(jstr).strip()
    if jstr[-1] in [",", ";"]:
        jstr = jstr[:-1].strip()
    jstr = jstr.replace(",}", "}")
    jstr = re.sub(r"\s+", " ", jstr)
    jstr = jstr.replace('" ', '"')
    jstr = jstr.replace(' "', '"')
    jstr = jstr.replace(", }", "}")
    jstr = re.sub(r"[a-zA-Z0-9]\}", '"}', jstr)
    jstr = re.sub(r":\s*(\w)", r': "\1', jstr)
    jstr = re.sub(r"\b0+(\d+)\b", r"\1", jstr)
    # jstr = re.sub(r"\s*([{}])\s*", r"\1", jstr)
    jstr = re.sub(r"\s*([:,])\s*", r"\1 ", jstr)
    jstr = re.sub(r",}", '"}', jstr)
    jstr = re.sub(r"\"+}", '"}', jstr)
    jstr = jstr.replace('""', '","')
    return jstr


def str_to_json(x, max_try=10):
    # jstr = json_str(x)
    jstr = x[x.find("{") : x.rfind("}") + 1]
    jstr = jstr.replace(': ",', ': "",')
    json_dict = {}
    tries = 0
    while True and tries < max_try:
        try:
            json_dict = json.loads(jstr)
            break
        except Exception as e:
            unexp = int(re.findall(r"\(char (\d+)\)", str(e))[0])
            unesc = jstr.rfind(r'"', 0, unexp)
            jstr = jstr[:unesc] + r"\"" + jstr[unesc + 1 :]
            closg = jstr.find(r'"', unesc + 2)
            jstr = jstr[:closg] + r"\"" + jstr[closg + 1 :]
            tries += 1
    return jstr, json_dict

# %% ../nbs/01_core.ipynb 11
def extract_text(path):
    data = pdfplumber.open(path)
    pdf_text = [p.extract_text(layout=True).splitlines() for p in data.pages]
    text = pdf_text[0]
    return text


def extract_order_docs(
    text,
    header_cols=["item", "description", "price", "quantity", "amount", "total", "qty"],
    get_parts=False,
    splitter=None,
    chunk_size=4000,
    chunk_overlap=0,
):
    if splitter is None:
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n"], chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
    avg_len = mode([len(t) for t in text])
    order_text = [text[0]]
    order_metadatas = [{}]
    desc = ""
    # for i, txt in enumerate(text[1:-1], start=1):
    for txt in text[1:-1]:
        if not len(txt) >= avg_len * 2:
            txt = txt.replace('"', "").replace("'", "").strip()
            if row_check(txt, header_cols, 2):
                order_text.append(txt)
                order_metadatas.append({})
            elif len(txt) < avg_len * 0.75 and not row_check(
                order_text[-1], header_cols, 2
            ):
                desc += " " + txt
            else:
                if len(desc) > 0:
                    order_metadatas.append({"desc": desc.strip()})
                    desc = ""
                if get_parts:
                    part_nums = [
                        x
                        for x in re.findall(r"\d{5}", txt)
                        if not x.startswith("00") and "." not in x
                    ]
                    if len(part_nums) == 0:
                        part_nums = [
                            x
                            for x in re.findall(r"\d{4}", txt)
                            if not x.startswith("00") and "." not in x
                        ]
                    if len(part_nums) > 0:
                        part_num = part_nums[0]
                        txt += f" part_number: {part_num}"
                order_text.append(txt)
    if len(desc) > 0:
        order_metadatas.append({"desc": desc.strip()})
    order_text.append(text[-1])
    order_metadatas += [{} for _ in range(len(order_text) - len(order_metadatas))]
    return splitter.create_documents(order_text, metadatas=order_metadatas)


def info_order_docs(
    text,
    header_cols=["item", "description", "price", "quantity", "amount", "total", "qty"],
    total_cols=["total", "subtotal", "tax"],
    chunk_size=4000,
    chunk_overlap=0,
    get_parts=False,
):
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"], chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    table_text, top_idx, bottom_idx = extract_sub_text(
        text,
        top_cols=header_cols,
        bottom_cols=total_cols,
        top_thresh=2,
        bottom_thresh=1,
        alt_top_index=0,
        alt_bottom_index=0,
    )

    top_text = [
        t.replace('"', "").replace("'", "").strip()
        for t in text[:top_idx]
        if len(t.strip()) > 0
    ]
    bottom_text = [
        t.replace('"', "").replace("'", "").strip()
        for t in text[bottom_idx:]
        if len(t.strip()) > 0
    ]
    info_text = top_text + bottom_text
    info_docs = splitter.create_documents(info_text)
    order_docs = extract_order_docs(
        table_text, header_cols=header_cols, get_parts=get_parts, splitter=splitter
    )
    return dict(info_docs=info_docs, order_docs=order_docs)


def pdf_to_info_order_docs(
    path,
    header_cols=["item", "description", "price", "quantity", "amount", "total", "qty"],
    total_cols=["total", "subtotal", "tax"],
    chunk_size=4000,
    chunk_overlap=0,
    get_parts=False,
):
    text = extract_text(path)
    return info_order_docs(
        text,
        header_cols=header_cols,
        total_cols=total_cols,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        get_parts=get_parts,
    )


# %% ../nbs/01_core.ipynb 14
def qa_llm_chain(model="meta-llama/Llama-2-7b-chat-hf"):
    token = "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"
    tokenizer = AutoTokenizer.from_pretrained(model, token=token)
    model = AutoModelForCausalLM.from_pretrained(model,device_map='auto', torch_dtype=torch.float16, token=token)
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map="auto",
        max_new_tokens=1024,
        do_sample=True,
        top_k=5,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
    )
    llm = HuggingFacePipeline(pipeline=pipe, model_kwargs={"temperature": 0})
    return load_qa_chain(llm, "stuff")


# %% ../nbs/01_core.ipynb 16
def fix_json(text):
    json_str = copy.deepcopy(text)
    if json_str.count("{") != json_str.count("}"):
        while json_str.count("{") % 2 != 0:
            json_str = "{" + json_str
            json_str = json_str.replace("}{", "},{")
        while json_str.count("}") % 2 != 0:
            json_str = json_str + "}"
            json_str = json_str.replace("}{", "},{")
    if json_str.count("{") < json_str.count("}"):
        while json_str.count("{") != json_str.count("}"):
            json_str = "{" + json_str
            json_str = json_str.replace("}{", "},{")
    elif json_str.count("{") > json_str.count("}"):
        while json_str.count("{") != json_str.count("}"):
            json_str = json_str + "}"
            json_str = json_str.replace("}{", "},{")
    json_str = json_str.replace("\n", "")
    if json_str.startswith("{{") and json_str.endswith("}}"):
        json_str = json_str[1:-1]
    json_str = json_str.replace('"""', '"')
    json_str = json_str.replace('""', '","')
    return json_str


def json_response(chain, docs, query, max_tries=6):
    tries = 0
    res = ""
    while res == "" and tries < max_tries:
        res = chain(dict(input_documents=docs, question=query))
        res = res["output_text"].strip()
        res = res[res.find("{") : res.rfind("}") + 1]
        tries += 1
    tries = 0
    while tries < max_tries:
        try:
            return dict(json_str=res, json=json.loads(fix_json(res)))
        except:
            tries += 1

    return dict(json_str=res, json={})


def info_json(chain, info_docs, max_tries=6):
    info_query = """Extract the order information like the numbers, dates, shipping address and total amount. Include the quote number too if found."""
    json_query = "\nReturn the text in JSON format. It must be compatible with json.loads."
    suffix = "\nDon't tell me how to do it, just do it. Don't add any disclaimer."
    info_query += json_query + suffix
    return json_response(chain, info_docs, info_query, max_tries)


def order_json(
    chain,
    order_docs,
    max_tries=6,
    get_parts=False,
    chunk_size=4000,
    chunk_overlap=0,
):
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"], chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    json_query = "\nReturn the text in JSON format. It must be compatible with json.loads."
    suffix = ("\nDon't tell me how to do it, just do it. Don't add any disclaimer.",)
    part_query = "Include the part numbers if defined."
    query = "Extract the order items with full details and descriptions and prices."
    if get_parts:
        query += " " + part_query
    query += suffix
    query = query.strip()
    items = chain(dict(input_documents=order_docs, question=query))["output_text"].strip()

    item_query = json_query
    if get_parts:
        item_query += " " + part_query
    item_query += suffix
    item_query = item_query.strip()

    item_docs = splitter.create_documents([items])
    return json_response(chain, item_docs, item_query, max_tries=max_tries)


def pdf_to_info_order_json(path, chain, max_tries=6, get_parts=False):
    info_order_dict = pdf_to_info_order_docs(path, get_parts=get_parts)
    info_dict = info_json(
        chain=chain, info_docs=info_order_dict["info_docs"], max_tries=max_tries
    )
    order_dict = order_json(
        chain=chain,
        order_docs=info_order_dict["order_docs"],
        max_tries=max_tries,
        get_parts=get_parts,
    )
    return {"info": info_dict, "order": order_dict}
