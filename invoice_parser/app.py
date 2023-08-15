from invoice_parser.imports import *
from invoice_parser.utils import *
from invoice_parser.core import *

from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form

app = FastAPI(
    title="Wilson Tools Parser",
    version="0.0.1",
)

llm_chain = qa_llm_chain()

@app.post("/parse_po")
def po_action(path: str):
    msg.info(f"Path: {path}", spaced=True)
    res = pdf_to_info_order_json(path, llm_chain, get_parts=True)
    res_json = {"info": res["info"]["json"], "order": res["order"]["json"]}
    return JSONResponse(content=res_json)


@app.post("/parse_ap")
def ap_action(path: str):
    msg.info(f"Path: {path}", spaced=True)
    res = pdf_to_info_order_json(path, llm_chain, get_parts=False)
    res_json = {"info": res["info"]["json"], "order": res["order"]["json"]}
    return JSONResponse(content=res_json)
