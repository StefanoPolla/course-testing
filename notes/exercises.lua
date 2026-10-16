-- Exercises page: write ::: {#exercise-list} ::: in the text (exercises.qmd).
-- At render time it is replaced by the exercises (::: {#exr-...} divs) of every lecture
-- chapter (lNN-*.qmd) listed in _quarto.yml, each with a link back to the original, so
-- the page updates itself when a chapter is published. Exercises must not contain
-- labelled elements (equations, figures): the copies drop the labels.

local function read_file(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local text = f:read("a")
  f:close()
  return text
end

local function chapters(project)
  local list = {}
  for line in (read_file(project .. "/_quarto.yml") or ""):gmatch("[^\n]+") do
    local file = line:match("^%s*%-%s+(l%d%d%-[%w_-]+%.qmd)%s*$")
    if file then table.insert(list, file) end
  end
  return list
end

local function strip_ids(blocks)
  local function clear(el)
    if el.identifier and el.identifier ~= "" then
      el.identifier = ""
      return el
    end
  end
  return pandoc.Blocks(blocks):walk {
    Div = clear, Span = clear, Header = clear, Table = clear, Figure = clear,
    Str = function(s) if s.text:match("^{#.*}$") then return {} end end,
  }
end

local function citation(id)
  return pandoc.Cite({ pandoc.Str("@" .. id) }, { pandoc.Citation(id, "NormalCitation") })
end

local function exercise_list(el)
  if el.identifier ~= "exercise-list" then return nil end
  local project = quarto.project.directory
  local out = pandoc.Blocks {}
  for number, file in ipairs(chapters(project)) do
    local text = (read_file(project .. "/" .. file) or ""):gsub("{{<.->}}", "")
    local doc = pandoc.read(text, "markdown")
    local title, found = nil, {}
    doc:walk {
      Header = function(h) if h.level == 1 and not title then title = h.content end end,
      Div = function(d) if d.identifier:match("^exr%-") then table.insert(found, d) end end,
    }
    if #found > 0 then
      local heading = pandoc.Inlines { pandoc.Str("Chapter " .. number .. ": ") }
      heading:extend(title or {})
      out:insert(pandoc.Header(2, heading, pandoc.Attr("", { "unnumbered" })))
      for _, d in ipairs(found) do
        local body = pandoc.Blocks(d.content)
        local label = pandoc.Inlines { pandoc.Strong { citation(d.identifier) } }
        if body[1] and body[1].t == "Header" then
          label:insert(pandoc.Str(" ("))
          label:extend(body[1].content)
          label:insert(pandoc.Str(")"))
          body:remove(1)
        end
        local copy = pandoc.Blocks { pandoc.Para(label) }
        copy:extend(strip_ids(body))
        out:insert(pandoc.Div(copy, pandoc.Attr("", { "exercise-copy" })))
      end
    end
  end
  return out
end

return { { Div = exercise_list } }
