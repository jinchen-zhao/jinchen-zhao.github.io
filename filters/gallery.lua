-- Side-by-side comparison gallery: one slide per field, advanced by tabs,
-- arrows, swipe or a timer (the script in templates/post.html).
--
--   ::: {.gallery}
--   ::: {.slide field="Physics" title="Paper title" venue="Nature Physics (2026)"
--        doi="10.1038/..." license="CC BY 4.0" authors="Smith et al."}   (url="https://..." where there is no DOI)
--   ![Published](gallery/phys-pub.jpg)
--   ![Our skill](gallery/phys-ours.jpg)
--   :::
--   :::
--
-- Each image becomes one panel, labelled by its alt text. Without JavaScript
-- the slides simply stack. An image title (![No skill](a.jpg "Prompt: …")) is
-- shown under that panel only, so each version can carry its own prompt.

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
      local note = ""
      if img.title and img.title ~= "" then note = '<p class="gallery-credit">' .. esc(img.title) .. "</p>" end
      local default = img.classes:includes("default") and " data-default" or "" -- the panel shown first
      panels[#panels + 1] = string.format(
        '<figure class="gallery-panel"' .. default .. '><a href="%s" target="_blank" rel="noopener">'
          .. '<img src="%s" alt="%s" loading="lazy"></a><figcaption>%s</figcaption>%s</figure>',
        esc(img.src), esc(img.src), esc(label .. " figure, " .. field), esc(label), note)
    end,
  }
  local credit = ""
  if a.title then
    local t = esc(a.title)
    if a.doi then
      t = string.format('<a href="https://doi.org/%s">%s</a>', esc(a.doi), t)
    elseif a.url then -- sources without a DOI (patents, government reports)
      t = string.format('<a href="%s">%s</a>', esc(a.url), t)
    end
    credit = t
    if a.authors then credit = esc(a.authors) .. ", " .. credit end -- CC BY asks to name the creators
    if a.venue then credit = credit .. ", <em>" .. esc(a.venue) .. "</em>" end
    credit = credit .. "."
    if a.license then
      local lic = esc(a.license)
      if a.license:sub(1, 9) == "CC BY 4.0" then -- link the licence deed, keep any note after it as text
        lic = '<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>' .. esc(a.license:sub(10))
      end
      credit = credit .. " Published figure: " .. lic .. "."
    end
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
