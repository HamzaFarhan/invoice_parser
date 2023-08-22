from invoice_parser.imports import *
from invoice_parser.utils import *
from invoice_parser.core import *
from fastapi.responses import JSONResponse
from invoice_parser.api.utils import endpoint
from langchain_ray.remote_utils import handle_input_path, is_bucket
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query

app = FastAPI(
    title="Wilson Tools Parser",
    version="0.0.1",
)

llm_chain = qa_llm_chain()


@app.post("/parse_po")
def po_action(path: str = Query(..., description="Path to PDF file.")):
    return endpoint(path, llm_chain, get_parts=True)
    # msg.info(f"Path: {path}", spaced=True)
    # path, bucket_path = handle_input_path(path)
    # path = Path(path) / Path(bucket_path).name
    # msg.info(f"Received path: {bucket_path}, Local Path: {path}", spaced=True)
    # res = pdf_to_info_order_json(path, llm_chain, get_parts=True, max_tries=1)
    # res_json = {"info": res["info"]["json"], "order": res["order"]["json"]}
    # for k,v in res_json.items():
    #     if len(v) == 0:
    #         raise HTTPException(status_code=500, detail=f"Unable to extract {k} information. Please try again.")
    # return JSONResponse(content=res_json)


@app.post("/parse_ap")
def ap_action(path: str = Query(..., description="Path to PDF file.")):
    return endpoint(path, llm_chain, get_parts=False)
    # msg.info(f"Path: {path}", spaced=True)
    # path, bucket_path = handle_input_path(path)
    # path = Path(path) / Path(bucket_path).name
    # msg.info(f"Received path: {bucket_path}, Local Path: {path}", spaced=True)
    # res = pdf_to_info_order_json(path, llm_chain, get_parts=False, max_tries=1)
    # res_json = {"info": res["info"]["json"], "order": res["order"]["json"]}
    # for k,v in res_json.items():
    #     if len(v) == 0:
    #         raise HTTPException(status_code=500, detail=f"Unable to extract {k} information. Please try again.")
    # # res_json["info"] = remove_total_keys(res_json["info"])
    # return JSONResponse(content=res_json)
