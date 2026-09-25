-- Number figures and resolve figure references, like \label / \ref in LaTeX.
--   ![Caption.](plot.svg){#fig:setup}        -> "Figure 1. Caption."
--   as shown in @fig:setup                    -> "as shown in Figure 1" (a link)
-- Runs before --citeproc, so @fig: keys never reach the bibliography.

local numbers = {}

local function number_figures(doc)
  local n = 0
  return doc:walk {
    Figure = function(fig)
      if not fig.identifier:match("^fig:") then return nil end
      n = n + 1
      numbers[fig.identifier] = n
      local long = fig.caption.long
      local label = pandoc.Strong { pandoc.Str("Figure " .. n .. ".") }
      if #long > 0 and (long[1].t == "Plain" or long[1].t == "Para") then
        long[1].content:insert(1, pandoc.Space())
        long[1].content:insert(1, label)
      else
        long:insert(1, pandoc.Plain { label })
      end
      fig.caption.long = long
      return fig
    end,
  }
end

local function resolve_refs(doc)
  return doc:walk {
    Cite = function(cite)
      if #cite.citations ~= 1 then return nil end
      local id = cite.citations[1].id
      if not id:match("^fig:") then return nil end
      local k = numbers[id]
      if not k then
        io.stderr:write("figures.lua: unknown figure reference @" .. id .. "\n")
        return pandoc.Strong { pandoc.Str("Figure ??") }
      end
      return pandoc.Link({ pandoc.Str("Figure\u{a0}" .. k) }, "#" .. id)
    end,
  }
end

function Pandoc(doc)
  return resolve_refs(number_figures(doc))
end
