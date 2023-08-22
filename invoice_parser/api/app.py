from invoice_parser.api.imports import *
from invoice_parser.api.utils import *
from invoice_parser.core import pdf_to_info_order_docs

app = FastAPI(
    title="Wilson Tools Parser",
    version="0.0.1",
)


@serve.deployment(
    autoscaling_config=dict(
        min_replicas=1, max_replicas=1, target_num_ongoing_requests_per_replica=1
    ),
    ray_actor_options=dict(num_cpus=10, num_gpus=1.0),
    health_check_period_s=10,
    health_check_timeout_s=60,
)
@serve.ingress(app)
class WTIngress:
    def __init__(self):
        self.llm_chain = qa_llm_chain()

    def check_health(self):
        msg.info("Checking Health...", spaced=True)
        path = "/opt/demo_files/pdf/wt7.pdf"
        path, bucket_path = handle_endpoint_path(path)
        res = pdf_to_info_order_docs(path, get_parts=True)
        try:
            if is_bucket(bucket_path):
                os.remove(path)
        except:
            pass
        msg.good("Health Check Passed!", spaced=True)
        return res

    @app.post("/parse_po")
    def po_action(self, path: str = Query(..., description="Path to PDF file.")):
        return endpoint(path, self.llm_chain, get_parts=True)

    @app.post("/parse_ap")
    def ap_action(self, path: str = Query(..., description="Path to PDF file.")):
        return endpoint(path, self.llm_chain, get_parts=False)


deployment_handle = WTIngress.bind()
