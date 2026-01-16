#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask entrypoint for AI Cover Studio
Wraps the Gradio app for deployment platforms
"""

from ai_cover_app import criar_interface

# Create the Gradio interface
demo = criar_interface()

# Expose the Flask app for WSGI servers
app = demo.app

if __name__ == "__main__":
    demo.launch(server_port=7861, share=False, inbrowser=True)
