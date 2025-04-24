import * as pdfjsLib from "pdfjs-dist";
import "pdfjs-dist/build/pdf"; // required
import "../pdf-worker"; // this sets up the worker

export const extractTextFromPdf = async (pdfFile) => {
  const arrayBuffer = await pdfFile.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

  const allText = [];
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    const strings = content.items.map((item) => item.str).filter(Boolean);
    allText.push(strings.join(" "));
  }

  return allText.join("\n");
};
