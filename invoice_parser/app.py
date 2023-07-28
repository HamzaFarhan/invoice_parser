from invoice_parser.imports import *
from invoice_parser.utils import *
from invoice_parser.core import *

from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form


class InvoiceData(BaseModel):
    pdf_path: str = Field(
        title="PDF Path",
        description="It can be a single PDF file or a directory of PDF files.",
        example="/media/hamza/data2/wilson_tools/pdf/wt1.pdf",
    )
    csv_path: str = Field(
        title="CSV Path",
        description="The path to the CSV folder where the extracted data will be saved.",
        example="/media/hamza/data2/wilson_tools/csv",
    )


class InvoiceFile(BaseModel):
    pdf_file: UploadFile = File(title="PDF File", description="The uploaded PDF file.")
    csv_path: str = Form(
        title="CSV Path",
        description="The path to the CSV folder where the extracted data will be saved.",
        example="/media/hamza/data2/wilson_tools/csv",
    )


app = FastAPI(
    title="Invoice Parser",
    description="Invoice Parser is a tool to extract data from invoices.",
    version="0.0.1",
)

device = default_device()
inv_model = load_invoice_model(device=device)
invoice_chain = is_invoice_chain(model=inv_model)

pdf_chain = pdf_to_dfs_chain(
    input_variables=["pdf"], output_variables=["info_df", "order_df"], verbose=False
)


@app.post("/parse")
def action(data: InvoiceData):
    msg.info(f"Data: {data}", spaced=True)
    input = {"pdf": data.pdf_path}
    res = conditional_chain(
        input,
        first_chain=invoice_chain,
        next_chains={"pdf_chain": pdf_chain},
        router=lambda x: "pdf_chain" if x["is_invoice"] else "invoice_chain",
    )
    if res is None:
        res = {"Not an invoice": True}
    else:
        os.makedirs(data.csv_path, exist_ok=True)
        info_df = res["info_df"]
        order_df = res["order_df"]
        info_path = Path(data.csv_path) / "info.csv"
        order_path = Path(data.csv_path) / "order.csv"
        info_df.to_csv(info_path, index=False)
        order_df.to_csv(order_path, index=False)
        res = {"info_path": str(info_path), "order_path": str(order_path)}
    return JSONResponse(content=res)


# @app.post("/parse_file")
# def action(data: InvoiceFile):
#     msg.info(f"Data: {data}", spaced=True)
#     input = {"pdf": data.pdf_path}
#     res = conditional_chain(
#         input,
#         first_chain=invoice_chain,
#         next_chains={"pdf_chain": pdf_chain},
#         router=lambda x: "pdf_chain" if x["is_invoice"] else "invoice_chain",
#     )
#     if res is None:
#         res = {"Not an invoice": True}
#     else:
#         os.makedirs(data.csv_path, exist_ok=True)
#         info_df = res["info_df"]
#         order_df = res["order_df"]
#         info_path = Path(data.csv_path) / "info.csv"
#         order_path = Path(data.csv_path) / "order.csv"
#         info_df.to_csv(info_path, index=False)
#         order_df.to_csv(order_path, index=False)
#         res = {"info_path": str(info_path), "order_path": str(order_path)}
#     return JSONResponse(content=res)
