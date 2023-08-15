from invoice_parser.api.imports import *

app = FastAPI(
    title="Wilson Tools Parser",
    version="0.0.1",
)


@serve.deployment(
    autoscaling_config=dict(
        min_replicas=1, max_replicas=1, target_num_ongoing_requests_per_replica=1
    ),
    ray_actor_options=dict(num_cpus=6, num_gpus=0.8),
    health_check_period_s=10,
    health_check_timeout_s=30,
)
@serve.ingress(app)
class WTIngress:
    def __init__(self):
        self.llm_chain = qa_llm_chain()

    @app.post("/parse_po")
    def po_action(self, path: str = Field(title="Path to PDF")):
        msg.info(f"Path: {path}", spaced=True)
        path, bucket_path = handle_input_path(path)
        msg.info(f"Received path: {bucket_path}, Local Path: {path}", spaced=True)
        res = pdf_to_info_order_json(path, self.llm_chain, get_parts=True)
        res_json = {"info": res["info"]["json"], "order": res["order"]["json"]}
        return JSONResponse(content=res_json)

    @app.post("/parse_ap")
    def ap_action(self, path: str = Field(title="Path to PDF")):
        msg.info(f"Path: {path}", spaced=True)
        path, bucket_path = handle_input_path(path)
        msg.info(f"Received path: {bucket_path}, Local Path: {path}", spaced=True)
        res = pdf_to_info_order_json(path, self.llm_chain, get_parts=False)
        res_json = {"info": res["info"]["json"], "order": res["order"]["json"]}
        return JSONResponse(content=res_json)
