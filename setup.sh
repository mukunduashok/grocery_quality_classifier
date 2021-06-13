mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = 80\n\
enableCORS = false\n\
" > ~/.streamlit/config.toml