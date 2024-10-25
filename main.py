import streamlit.web.bootstrap

if __name__ == "__main__":
    # Initialize Streamlit with proper configuration
    streamlit.web.bootstrap.run(
        'streamlit_app.py',
        is_hello=False,
        args=[],
        flag_options={
            'server.port': 8501,
            'server.address': '0.0.0.0',
            'server.headless': True,
            'server.enableCORS': True,
            'server.enableXsrfProtection': True
        }
    )
