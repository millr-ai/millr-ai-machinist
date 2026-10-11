# Notices

Millr, the AI Machinist is copyright (c) 2026 Millr Inc. and licensed under the PolyForm Shield License 1.0.0 (LICENSE.txt).

Millr ships no CAD-reading or measuring code. When Claude measures a part it uses whatever CAD library is available where it runs, installing one if it must; Open CASCADE Technology, through one of its Python bindings, is a common choice, governed by the GNU Lesser General Public License version 2.1 with the Open CASCADE Exception (dev.opencascade.org/resources/licensing).

scripts/export_pdf.py and scripts/sheet.py use numpy, matplotlib, reportlab and Pillow, installed separately, to draw the PDF and the review sheet; scripts/look.js uses playwright-core and a Chromium where one exists. None of them ships with Millr.

## three.js

assets/three.min.js is three.js r128, unmodified: build/three.min.js from the npm package three@0.128.0 (https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js; MD5 eb8549863a97355411c3259a3f93b8e1, SHA-256 9274bbcec8d96168626c732b5d31c775aa8cfb7eaa0599bec0c175908a2c1ce2). The review page carries it inside it. Its license:

The MIT License

Copyright © 2010-2021 three.js authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
