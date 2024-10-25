import streamlit.web.bootstrap
import os

if __name__ == "__main__":
    # Set Streamlit configuration via environment variables
    os.environ['STREAMLIT_SERVER_PORT'] = '5000'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'  # Disable XSRF to allow CORS
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    try:
        streamlit.web.bootstrap.run(
            "streamlit_app.py",
            is_hello=False,
            args=[],
            flag_options={
                'server.port': 5000,
                'server.address': '0.0.0.0',
                'server.headless': True,
                'server.enableXsrfProtection': False,  # Disable XSRF to allow CORS
                'server.enableCORS': True,
                'browser.gatherUsageStats': False
            }
        )
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
