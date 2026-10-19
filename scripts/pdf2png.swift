// PDF の各ページを PNG にする(目視検証用)。 usage: swift pdf2png.swift in.pdf outdir [width]
import AppKit
import PDFKit
let a = CommandLine.arguments
guard a.count >= 3, let doc = PDFDocument(url: URL(fileURLWithPath: a[1])) else { print("usage: in.pdf outdir [width]"); exit(1) }
let out = URL(fileURLWithPath: a[2]); try? FileManager.default.createDirectory(at: out, withIntermediateDirectories: true)
let W = a.count > 3 ? Double(a[3])! : 1600
for i in 0..<doc.pageCount {
  let p = doc.page(at: i)!; let r = p.bounds(for: .mediaBox); let s = W / r.width
  let img = NSImage(size: NSSize(width: r.width * s, height: r.height * s))
  img.lockFocus(); NSColor.white.set(); NSRect(origin: .zero, size: img.size).fill()
  let ctx = NSGraphicsContext.current!.cgContext; ctx.scaleBy(x: s, y: s); p.draw(with: .mediaBox, to: ctx); img.unlockFocus()
  let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
  try! rep.representation(using: .png, properties: [:])!.write(to: out.appendingPathComponent(String(format: "page-%02d.png", i + 1)))
}
print("\(doc.pageCount) pages")
