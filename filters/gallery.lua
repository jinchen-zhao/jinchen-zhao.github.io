-- Side-by-side comparison gallery: one slide per field, advanced by tabs,
-- arrows, swipe or a timer (the script in templates/post.html).
--
--   ::: {.gallery}
--   ::: {.slide field="Physics" title="Paper title" venue="Nature Physics (2026)"
--        doi="10.1038/..." license="CC BY 4.0"}
--   ![Published](gallery/phys-pub.jpg)
--   ![Our skill](gallery/phys-ours.jpg)
--   :::
--   :::
--
-- Each image becomes one panel, labelled by its alt text. Without JavaScript
-- the slides simply stack.

local function esc(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function slide_html(div)
  local a = div.attributes
  local field = a.field or "Example"
  local panels = {}
  div:walk {
    Image = function(img)
      local label = pandoc.utils.stringify(img.caption)
      panels[#panels + 1] = string.format(
        '<figure class="gallery-panel"><a href="%s" target="_blank" rel="noopener">'
          .. '<img src="%s" alt="%s" loading="lazy"></a><figcaption>%s</figcaption></figure>',
        esc(img.src), esc(img.src), esc(label .. " figure, " .. field), esc(label))
    end,
  }
  local credit = ""
  if a.title then
    local t = esc(a.title)
    if a.doi then
      t = string.format('<a href="https://doi.org/%s">%s</a>', esc(a.doi), t)
    end
    credit = t
    if a.venue then credit = credit .. ", <em>" .. esc(a.venue) .. "</em>" end
    credit = credit .. "."
    if a.license then credit = credit .. " Published figure: " .. esc(a.license) .. "." end
    credit = '<p class="gallery-credit">' .. credit .. "</p>"
  end
  return string.format(
    '<section class="gallery-slide" data-field="%s" aria-roledescription="slide" aria-label="%s">'
      .. '<div class="gallery-pair">%s</div>%s</section>',
    esc(field), esc(field), table.concat(panels), credit)
end

function Div(div)
  if not div.classes:includes("gallery") then return nil end
  local slides = {}
  for _, block in ipairs(div.content) do
    if block.t == "Div" and block.classes:includes("slide") then
      slides[#slides + 1] = slide_html(block)
    end
  end
  return pandoc.RawBlock("html",
    '<div class="gallery" aria-roledescription="carousel">' .. table.concat(slides) .. "</div>")
end
