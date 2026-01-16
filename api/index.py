#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastAPI entrypoint for Vercel deployment
Mounts the Gradio app on FastAPI
"""

from fastapi import FastAPI
import gradio as gr
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_cover_app import criar_interface

# Create the FastAPI app
app = FastAPI(title="AI Cover Studio")

# Create the Gradio interface
demo = criar_interface()

# Mount Gradio on FastAPI
app = gr.mount_gradio_app(app, demo, path="/")
