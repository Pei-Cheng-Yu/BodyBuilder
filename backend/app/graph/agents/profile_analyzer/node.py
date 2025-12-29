from app.graph.llm.gemini import get_gemini
from app.graph.schema import InbodyMetrics
from app.graph.state import GraphState
from langchain_core.messages import SystemMessage

from .prompt import INBODY_ANALYZE_PROMPT
from .utils import get_inbody_analysis_message


def inbody_analysis_node(state: GraphState):
    llm = get_gemini()
    structured_llm = llm.with_structured_output(InbodyMetrics)

    sys_msg = SystemMessage(INBODY_ANALYZE_PROMPT)

    pdf_source = state.get("inbody_pdf_input")

    user_msg = get_inbody_analysis_message(pdf_source)
    if user_msg is None:
        print("❌ Error: user_msg is None. Skipping LLM call.")
    try:
        extracted_data = structured_llm.invoke([sys_msg, user_msg])

        current_profile = state.get("profile")
        if current_profile:
            updated_profile = current_profile.model_copy(
                update={"latest_scan": extracted_data}
            )
            return {
                "profile": updated_profile,
                "inbody_pdf_input": None,
                "is_dirty": True,
                "system_feedback": "📊 Successfully upate your body composition and stats",
            }

        return {
            "latest_scan_data": extracted_data,
            "inbody_pdf_input": None,
            "is_dirty": True,
            "system_feedback": "📊 Successfully create your body composition and stats",
        }

    except Exception as e:
        print(f"❌ LLM Invocation Failed: {e}")
        return {"system_feedback": str(e)}
