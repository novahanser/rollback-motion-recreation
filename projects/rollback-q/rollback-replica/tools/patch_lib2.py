p = r'C:\Users\bg931\Documents\New project\rollback-replica\scripts\lib.py'
s = open(p, encoding='utf-8').read()
a = s.index("    def flash(self, f, color, n=2):")
b = s.index("    def wipe(self, f, d, angle=90.0")
new = '''    def flash(self, f, color, n=2):
        """solid-colour silhouette for the first n frames (Tint effect: both map colours = colour, amount 100 -> 0)"""
        return self.flashes([(f, color), (f + n, None)])

    def flashes(self, steps):
        """steps: [(frame, colour or None)] sequence of silhouette colours; None = the real texture"""
        self.t_in = steps[0][0] if self.t_in == 0 else min(self.t_in, steps[0][0])
        col_keys, amt_keys = [], []
        for f, c in steps:
            if c is None:
                amt_keys.append((f, 0.0, HOLD))
            else:
                amt_keys.append((f, 100.0, HOLD))
                col_keys.append((f, [c[0] / 255.0, c[1] / 255.0, c[2] / 255.0, 1.0], HOLD))
        props = {'ADBE Tint-0003': amt_keys}
        if len(col_keys) == 1:
            props['ADBE Tint-0001'] = col_keys[0][1]
            props['ADBE Tint-0002'] = col_keys[0][1]
        elif col_keys:
            props['ADBE Tint-0001'] = col_keys
            props['ADBE Tint-0002'] = list(col_keys)
        self.effects.append({'match': 'ADBE Tint', 'props': props})
        return self

'''
s = s[:a] + new + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
