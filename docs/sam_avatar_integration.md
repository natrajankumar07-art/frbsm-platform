# SAM Avatar Integration — Epic 4D.1

**Date:** 2026-07-01  
**Tag:** `v0.5.1-sam-avatar`

---

## 1. Summary

The official SAM avatar (`apps/web/src/assets/avatars/sam.png`, 1254×1254 RGB PNG) has been integrated across every surface in the FRBSM AI Copilot that represents the SAM agent. The placeholder "S" character has been removed from all locations.

**Build:** Clean — 0 TypeScript errors, 0 Vite warnings.  
**Backend:** No backend changes — pure frontend work.  
**API:** No API changes.

---

## 2. New Component — `SamAvatar`

**File:** `apps/web/src/components/copilot/SamAvatar.tsx`

Single source of truth for the SAM avatar image. Every surface imports `SamAvatar` — changing the image file propagates everywhere automatically.

### Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `size` | `"xs" \| "sm" \| "md" \| "lg"` | `"sm"` | Pixel sizes: xs=28, sm=32, md=40, lg=64 (40 mobile) |
| `glow` | `boolean` | `true` | Soft blue glow: `box-shadow 0 0 8–14px rgba(43,91,215,0.30–0.40)` |
| `statusDot` | `boolean` | `false` | Green online dot, bottom-right |
| `className` | `string` | `""` | Additional container classes |

### Styling

```
rounded-full         — circular crop
border-2 border-white — thin white border
shadow-[0_0_Xpx_rgba(43,91,215,Y)]  — soft blue glow (accent #2B5BD7)
hover:scale-105      — scale up on hover
hover:shadow-[...]   — deepen glow on hover
transition-all duration-200  — smooth animation
```

### Accessibility

```html
<img alt="SAM – Supervisory AI Manager" … />
```

---

## 3. Updated Components — `AgentProfile`

**File:** `apps/web/src/components/copilot/AgentProfile.tsx`

Now uses `SamAvatar` internally. Profile displays:

```
[avatar]  SAM
          Supervisory AI Manager
          Senior Banking Intelligence Advisor
          ● Online
```

Added `subtitle` prop (default: `"Senior Banking Intelligence Advisor"`).  
Status dot is always green ("Online") for `active` and `idle` states.

---

## 4. Avatar Placement Map

| Surface | Component | Size | Status Dot | Glow |
|---|---|---|---|---|
| AI Copilot header | `AgentProfile` (compact) | sm (32px) | Yes | No |
| Conversation sidebar header | `SamAvatar` (direct) | sm (32px) | Yes | Yes |
| Conversation sidebar session items | `SamAvatar` (direct) | xs (28px) | No | No |
| Beside every assistant response | `ChatMessage` → `SamAvatar` | xs (28px) | No | No |
| Thinking indicator | `CopilotPage` → `SamAvatar` | xs (28px) | No | No |
| Planner panel header | `PlannerPanel` → `SamAvatar` | xs (28px) | Yes | Yes |
| Execution timeline header | `ExecutionTimeline` → `SamAvatar` | xs (28px) | Yes | Yes |
| Execution timeline empty state | `ExecutionTimeline` → `SamAvatar` | md (40px) | Yes | Yes |
| Report generation panel header | `ReportPanel` → `SamAvatar` | xs (28px) | Yes | Yes |

---

## 5. Responsive Behaviour

| Mode | Size in `SamAvatar` lg | Notes |
|---|---|---|
| Mobile (`< sm` breakpoint) | 40×40 px | `w-10 h-10` |
| Desktop (`≥ sm` breakpoint) | 64×64 px | `sm:w-16 sm:h-16` |

Smaller sizes (xs, sm, md) are fixed pixel sizes and do not change between breakpoints.

---

## 6. Build Verification

```
✓ 2995 modules transformed
✓ dist/assets/sam-BCOEYPAQ.png  1,771.84 kB  (Vite fingerprinted asset)
✓ built in 2.86s
TypeScript: 0 errors
```

PNG type declarations added to `apps/web/src/vite-env.d.ts`:

```typescript
declare module "*.png" {
  const src: string;
  export default src;
}
```

---

## 7. Files Changed

| File | Type | Change |
|---|---|---|
| `apps/web/src/components/copilot/SamAvatar.tsx` | New | Reusable avatar component |
| `apps/web/src/components/copilot/AgentProfile.tsx` | Modified | Uses `SamAvatar`, adds `subtitle` prop, "Online" status |
| `apps/web/src/components/copilot/ChatMessage.tsx` | Modified | SAM avatar beside assistant messages |
| `apps/web/src/components/copilot/PlannerPanel.tsx` | Modified | SAM avatar in panel header |
| `apps/web/src/components/copilot/ExecutionTimeline.tsx` | Modified | SAM avatar in header and empty state |
| `apps/web/src/components/copilot/ReportPanel.tsx` | Modified | SAM avatar in panel header |
| `apps/web/src/pages/copilot/CopilotPage.tsx` | Modified | SAM avatar in sidebar header + session list |
| `apps/web/src/vite-env.d.ts` | New | PNG module type declaration |

---

*No backend, API, or test changes.*
