from invoice_parser.api.imports import *


def handle_endpoint_path(path):
    path, bucket_path = handle_input_path(path)
    if is_bucket(bucket_path):
        path = Path(path) / Path(bucket_path).name
    msg.info(f"Received path: {bucket_path}, Local Path: {path}", spaced=True)
    return path, bucket_path


def endpoint(path, llm_chain, get_parts=True):
    msg.info(f"Path: {path}", spaced=True)
    path, bucket_path = handle_endpoint_path(path)
    # path, bucket_path = handle_input_path(path)
    # if is_bucket(bucket_path):
    #     path = Path(path) / Path(bucket_path).name
    # msg.info(f"Received path: {bucket_path}, Local Path: {path}", spaced=True)
    res_json = pdf_to_data_json(path, llm_chain, max_tries=2, get_parts=get_parts)
    # res = pdf_to_info_order_json(path, llm_chain, get_parts=get_parts, max_tries=1)
    try:
        if is_bucket(bucket_path):
            os.remove(path)
    except:
        pass
    # res_json = {"info": res["info"]["json"], "order": res["order"]["json"]}
    for k, v in res_json.items():
        if len(v) == 0:
            raise HTTPException(
                status_code=500, detail=f"Unable to extract {k} information. Please try again."
            )
    return JSONResponse(content=res_json)
