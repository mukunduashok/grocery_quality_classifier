# Reference: https://gist.github.com/tvst/036da038ab3e999a64497f42de966a92#gistcomment-3778125-permalink
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
from types import SimpleNamespace


def get_state(**default_values):
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Could not get your Streamlit session instance.")

    if not hasattr(session_info.session, "_custom_state"):
        session_info.session._custom_state = SimpleNamespace(**default_values)

    return session_info.session._custom_state
