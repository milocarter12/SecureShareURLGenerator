import streamlit.web.bootstrap

if __name__ == "__main__":
    streamlit.web.bootstrap.run(
        "streamlit_app.py",      # Script path
        is_hello=False,          # Not a hello script
        args=[],                 # Args list
        flag_options={}          # Flag options dict
    )
