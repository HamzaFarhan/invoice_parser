from invoice_parser.imports import *
from invoice_parser.utils import *
from invoice_parser.core import *
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form
from langchain_ray.remote_utils import handle_input_path

app = FastAPI(
    title="Wilson Tools Parser",
    version="0.0.1",
)

llm_chain = qa_llm_chain()


@app.post("/parse_po")
def po_action(path: str):
    msg.info(f"Path: {path}", spaced=True)
    path, bucket_path = handle_input_path(path)
    path = Path(path) / Path(bucket_path).name
    msg.info(f"Received path: {bucket_path}, Local Path: {path}", spaced=True)
    res = pdf_to_info_order_json(path, llm_chain, get_parts=True)
    res_json = {"info": res["info"]["json"], "order": res["order"]["json"]}
    res_json["info"] = remove_total_keys(res_json["info"])
    return JSONResponse(content=res_json)


@app.post("/parse_ap")
def ap_action(path: str):
    msg.info(f"Path: {path}", spaced=True)
    path, bucket_path = handle_input_path(path)
    path = Path(path) / Path(bucket_path).name
    msg.info(f"Received path: {bucket_path}, Local Path: {path}", spaced=True)
    res = pdf_to_info_order_json(path, llm_chain, get_parts=False)
    res_json = {"info": res["info"]["json"], "order": res["order"]["json"]}
    res_json["info"] = remove_total_keys(res_json["info"])
    return JSONResponse(content=res_json)
