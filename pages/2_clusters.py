import streamlit as st
from engine1 import run_engine1
from schemas import Engine1Cluster, OwnedSystem, UseCase

st.title("2. Engine 1 · Cluster and check what exists")
raw_use_cases = st.session_state.get("engine1_use_cases", [])
raw_systems = st.session_state.get("engine1_systems", [])

if not raw_use_cases:
    st.warning("Complete Intake first and load the repository input.")
    st.stop()

st.write(f"Input: **{len(raw_use_cases)} use cases** and **{len(raw_systems)} owned systems**")
if st.button("Run Engine 1", type="primary"):
    use_cases = [UseCase.model_validate(item) for item in raw_use_cases]
    systems = [OwnedSystem.model_validate(item) for item in raw_systems]
    result = run_engine1(use_cases, systems)
    st.session_state["clusters"] = [item.model_dump(mode="json") for item in result]
    st.session_state["interviews_by_cluster"] = {}
    st.success(f"Engine 1 created {len(result)} clusters. Engine 2 is now unlocked.")

clusters = st.session_state.get("clusters", [])
if not clusters:
    st.info("Run Engine 1 to create clusters and unlock Engine 2.")
else:
    for raw_cluster in clusters:
        cluster = Engine1Cluster.model_validate(raw_cluster)
        with st.expander(f"{cluster.cluster_id} - {cluster.cluster_name}", expanded=True):
            st.write(f"**Underlying need:** {cluster.underlying_need}")
            st.write(f"**Member use cases:** {', '.join(map(str, cluster.member_use_cases))}")
            st.write(f"**Existing-system candidates:** {', '.join(cluster.owned_system_candidates) or 'None'}")
            st.write(f"**Missing information:** {', '.join(cluster.missing_information) or 'None'}")
