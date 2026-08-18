# -*- coding: utf-8 -*-
def _unlock_homepage_noupdate(env):
    """Allow homepage XML to refresh on every module upgrade."""
    env['ir.model.data'].search([
        ('module', '=', 'website_kad_global'),
        ('name', '=', 'page_home'),
    ]).write({'noupdate': False})


def _sync_website_menus(env):
    """Keep public nav labels aligned after upgrades (menu XML is noupdate)."""
    Menu = env['website.menu'].sudo()
    Data = env['ir.model.data'].sudo()
    updates = {
        'menu_kad_about': ('About Us', '/#about', 10),
        'menu_kad_services': ('Services', '/#services', 20),
        'menu_kad_exports': ('Exports', '/#exports', 30),
        'menu_kad_imports': ('Imports', '/#imports', 40),
        'menu_kad_why': ('Why KAD', '/#why-us', 50),
        'menu_kad_contact': ('Contact', '/#contact', 80),
    }
    for xmlid, (name, url, sequence) in updates.items():
        rec = Data.search([('module', '=', 'website_kad_global'), ('name', '=', xmlid)], limit=1)
        if rec:
            rec.write({'noupdate': False})
            menu = env.ref(f'website_kad_global.{xmlid}', raise_if_not_found=False)
            if menu:
                menu.write({'name': name, 'url': url, 'sequence': sequence})

    extra = [
        ('menu_kad_markets', 'Global Markets', '/#markets', 60),
        ('menu_kad_quote', 'Request Quote', '/#quote', 70),
    ]
    website = env['website'].search([], limit=1)
    parent = env.ref('website.main_menu', raise_if_not_found=False)
    if not website or not parent:
        return
    for xmlid, name, url, sequence in extra:
        existing = env.ref(f'website_kad_global.{xmlid}', raise_if_not_found=False)
        if existing:
            existing.write({'name': name, 'url': url, 'sequence': sequence})
            continue
        menu = Menu.create({
            'name': name,
            'url': url,
            'parent_id': parent.id,
            'website_id': website.id,
            'sequence': sequence,
        })
        Data.create({
            'module': 'website_kad_global',
            'name': xmlid,
            'model': 'website.menu',
            'res_id': menu.id,
            'noupdate': False,
        })


def post_init_hook(env):
    _unlock_homepage_noupdate(env)
    _sync_website_menus(env)


def uninstall_hook(env):
    pass
