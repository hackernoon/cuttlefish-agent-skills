---
name: pixel-icon-library
description: Use when adding icons to a website, app or design that wants a retro pixel-art look — installs and uses HackerNoon's open-source Pixel Icon Library (24px grid, solid/regular/social variants) via npm, CSS classes, React or raw SVG, with correct CC BY 4.0 attribution.
---

# HackerNoon Pixel Icon Library

Open-source pixelated icons designed on a 24px grid. Site: https://pixeliconlibrary.com · Repo: https://github.com/hackernoon/pixel-icon-library · npm: `@hackernoon/pixel-icon-library`

## Install

```bash
npm i @hackernoon/pixel-icon-library
```

## Use as an icon font (HTML)

```html
<link rel="stylesheet" href="node_modules/@hackernoon/pixel-icon-library/fonts/iconfont.css">
<i class="hn hn-icon-name"></i>
```

## React

```jsx
import '@hackernoon/pixel-icon-library/fonts/iconfont.css';
export const Icon = ({ name }) => <i className={`hn hn-${name}`} aria-hidden="true" />;
```

## Raw SVG

Prefer the SVG files in `icons/` when you need to recolor with `currentColor`, inline the icon, or ship only a few icons. Use `<img src="…/icon.svg" alt="…">` for decorative-but-meaningful icons and inline `<svg>` when it must inherit text color.

## Rules

1. Pick icon names from https://pixeliconlibrary.com (search there, then use the `hn-` class shown). Don't guess names; if unsure, check `fonts/iconfont.css` for the class list.
2. Keep icons on multiples of the 24px grid (12, 24, 48) so pixels stay crisp; set `image-rendering: pixelated` on scaled PNGs.
3. Decorative icons get `aria-hidden="true"`; icon-only buttons need an `aria-label`.
4. **Attribution is required.** Icons are CC BY 4.0. Add a credit such as: `Icons by HackerNoon's Pixel Icon Library (pixeliconlibrary.com), CC BY 4.0` in the footer, about page or credits. Other repo files are MIT. Projects that can't attribute can buy a license at https://pixeliconlibrary.com/license/.
