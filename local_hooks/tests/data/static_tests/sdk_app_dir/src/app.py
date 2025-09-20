from soar_sdk import App

app = App(
    name="test",
    app_type="generic",
    logo="logo.svg",
    logo_dark="logo_dark.svg",
    product_vendor="Generic",
    product_name="HTTP",
    publisher="Splunk",
    appid="290b7499-0374-4930-9cdc-5e9b05d65827",
    fips_compliant=False,
)


@app.action
def test_connectivity(config):
    return True
