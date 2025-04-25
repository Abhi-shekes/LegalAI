from fastapi import APIRouter, HTTPException, Request, Depends
import torch
import json
from sqlalchemy import select
from app.auth import get_current_user
from app.database import database
from app.models import CaseInput, UserOut
from app.schemas import generated_arguments

router = APIRouter()

@router.post("/generate")
async def generate_arguments(
    case: CaseInput, 
    request: Request,
    current_user: UserOut = Depends(get_current_user)
):
    try:
        tokenizer = request.app.state.tokenizer
        model = request.app.state.model

        prompt = f"""### Case ID:
{case.case_id}

### Facts:
{case.facts.strip() if case.facts else 'No facts provided.'}

### IPC Sections:
{chr(10).join(map(str, case.ipc_sections)) if case.ipc_sections else 'No IPC sections provided.'}

### Generate Arguments and Counter Arguments:
"""

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=case.max_new_tokens,
                temperature=case.temperature,
                top_p=case.top_p,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        gen_text = tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)

        try:
            gen_json = json.loads(gen_text.strip())  # Attempt parsing
        except json.JSONDecodeError:
            gen_json = {"raw_text": gen_text.strip()}  # fallback to plain text

        query = generated_arguments.insert().values(
            user_id=current_user.id,
            case_id=case.case_id,
            generated_arguments=json.dumps(gen_json)  # store as JSON string
        )
        await database.execute(query)

        return {"case_id": case.case_id, "generated_arguments": gen_json}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generated_arguments/{case_id}")
async def get_generated_arguments(case_id: str, current_user: UserOut = Depends(get_current_user)):
    query = select(generated_arguments).where(
        generated_arguments.c.case_id == case_id,
        generated_arguments.c.user_id == current_user.id
    )
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="Generated arguments not found for this case")
    
    try:
        parsed = json.loads(result["generated_arguments"])
    except (TypeError, json.JSONDecodeError):
        parsed = {"raw_text": result["generated_arguments"]}

    return {"case_id": case_id, "generated_arguments": parsed}
