import streamlit as st

st.title("teste do streamlit")

contador_normal = 0
if "contador" not in st.session_state:
    st.session_state.contador = 0

if st.button("carrega aqui"):
    contador_normal +=1
    st.session_state.contador +=1

st.write("variavel normal:", contador_normal)
st.write("session_state:", st.session_state.contador)

