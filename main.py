import streamlit.web.bootstrap
import os

if __name__ == "__main__":
    os.environ['STREAMLIT_SERVER_PORT'] = '5000'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'true'
    os.environ['STREAMLIT_SERVER_BASE_URL_PATH'] = ''

    # Initialize Streamlit with proper configuration
    streamlit.web.bootstrap.run(
        'streamlit_app.py',
        is_hello=False,
        args=[],
        flag_options={
            'server.port': 5000,
            'server.address': '0.0.0.0',
            'server.headless': True,
            'server.enableCORS': True,
            'server.enableXsrfProtection': True,
            'server.baseUrlPath': '',
            'server.maxUploadSize': 5
        }
    )
