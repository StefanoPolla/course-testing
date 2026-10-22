-- Temporary review aid: shows text changed in a review round in a different colour.
-- Write [changed text]{.chg} inline, or ::: {.chg} ... ::: around whole blocks.
-- Once the changes are accepted, remove the markers and this filter (_quarto.yml).
local used = false

local function latex() return quarto.doc.is_format("latex") end

local function span(el)
  if not el.classes:includes("chg") then return nil end
  used = true
  if latex() then
    local out = pandoc.List { pandoc.RawInline("latex", "{\\color{chg}") }
    out:extend(el.content)
    out:insert(pandoc.RawInline("latex", "}"))
    return out
  end
end

local function div(el)
  if not el.classes:includes("chg") then return nil end
  used = true
  if latex() then
    return { pandoc.RawBlock("latex", "\\begingroup\\color{chg}"), el,
             pandoc.RawBlock("latex", "\\endgroup") }
  end
end

local function header(doc)
  if not used then return nil end
  if latex() then
    quarto.doc.include_text("in-header",
      "\\usepackage{xcolor}\\definecolor{chg}{HTML}{A3236B}")
  elseif quarto.doc.is_format("html") then
    quarto.doc.include_text("in-header", [[
<style>
  .chg { color: #a3236b; }
  body.quarto-dark .chg { color: #ff8cc6; }
  div.chg { border-left: 3px solid currentColor; padding-left: 0.6em; }
</style>]])
  end
end

return {
  { Span = span, Div = div },
  { Pandoc = header },
}
