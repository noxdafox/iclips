FROM jupyter/minimal-notebook

EXPOSE 8888

# Install Python packages
RUN python3 -m pip install --upgrade pip
RUN pip3 install --upgrade iclips

CMD ["jupyter", "notebook", "--no-browser", "--ip", "0.0.0.0", "--port=8888"]
