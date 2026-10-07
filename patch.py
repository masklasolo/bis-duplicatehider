# BiS fixes for DuplicateHider (applied on top of the pinned upstream commit)
import io

def load(p):
    return io.open(p, encoding='utf-8-sig', newline='').read()

def save(p, s):
    io.open(p, 'w', encoding='utf-8-sig', newline='').write(s)

def rep(s, a, b):
    assert s.count(a) == 1, (a, s.count(a))
    return s.replace(a, b)

I = '            '
p = 'up/source/DuplicateHiderPlugin.cs'
s = load(p)
nl = '\r\n' if '\r\n' in s else '\n'
s = s.replace('\r\n', '\n')

# 1. copies are known only at this point - tell the UI, otherwise the first game shows a single icon
s = rep(s, I + '// QuickSearch support',
        I + 'GroupUpdated?.Invoke(this, PlayniteApi.Database.Games.Select(g => g.Id));\n' + I + '// QuickSearch support')

# 2. handlers re-subscribe even when something throws
s = rep(s, I + 'var toUpdate = new List<Game>();\n' + I + 'var toUpdateGroups',
        I + 'try\n' + I + '{\n' + I + 'var toUpdate = new List<Game>();\n' + I + 'var toUpdateGroups')
s = rep(s, I + 'PlayniteApi.Database.Games.ItemUpdated += Games_ItemUpdated;\n' + I + 'PlayniteApi.Database.Games.ItemCollectionChanged += Games_ItemCollectionChanged;\n        }',
        I + '}\n' + I + 'catch (Exception ex) { logger.Error(ex, "BiS: ItemCollectionChanged failed"); }\n' + I + 'finally\n' + I + '{\n'
        + I + 'PlayniteApi.Database.Games.ItemUpdated += Games_ItemUpdated;\n' + I + 'PlayniteApi.Database.Games.ItemCollectionChanged += Games_ItemCollectionChanged;\n' + I + '}\n        }')
s = rep(s, I + 'IFilter<IEnumerable<Game>> gameFilter = GetGameFilter();\n' + I + 'IFilter<string> nameFilter = GetNameFilter();\n' + I + 'if (settings.AddHiddenToIgnoreList)',
        I + 'try\n' + I + '{\n' + I + 'IFilter<IEnumerable<Game>> gameFilter = GetGameFilter();\n' + I + 'IFilter<string> nameFilter = GetNameFilter();\n' + I + 'if (settings.AddHiddenToIgnoreList)')
s = rep(s, I + '}\n' + I + 'PlayniteApi.Database.Games.ItemUpdated += Games_ItemUpdated;\n        }',
        I + '}\n' + I + '}\n' + I + 'catch (Exception ex) { logger.Error(ex, "BiS: ItemUpdated failed"); }\n' + I + 'finally\n' + I + '{\n'
        + I + 'PlayniteApi.Database.Games.ItemUpdated += Games_ItemUpdated;\n' + I + '}\n        }')

# 3. refresh copies and icons for added and removed games too
s = rep(s, I + 'if (toUpdate.Count > 0)\n' + I + '{\n' + I + '    var filter = GetGameFilter();',
        I + 'if (toUpdate.Count > 0 || e.AddedItems.Count > 0 || e.RemovedItems.Count > 0)\n' + I + '{\n' + I + '    var filter = GetGameFilter();')
s = rep(s, I + '    PlayniteApi.Database.Games.Update(toUpdate);\n' + I + '    UpdateGuidToCopiesDict(updatedIds);',
        I + '    if (toUpdate.Count > 0) { PlayniteApi.Database.Games.Update(toUpdate); }\n' + I + '    UpdateGuidToCopiesDict(updatedIds);')
save(p, s.replace('\n', nl))

# 4. Uninstall command really uninstalls
p = 'up/source/Models/ListData.cs'
s = load(p)
assert s.count('new RelayCommand(() => DuplicateHiderPlugin.API.InstallGame(Game.Id));') == 4
s = s.replace('UninstallCommand = new RelayCommand(() => DuplicateHiderPlugin.API.InstallGame(Game.Id));',
              'UninstallCommand = new RelayCommand(() => DuplicateHiderPlugin.API.UninstallGame(Game.Id));')
s = s.replace('uninstallCommand ?? new RelayCommand(() => DuplicateHiderPlugin.API.InstallGame(Game.Id));',
              'uninstallCommand ?? new RelayCommand(() => DuplicateHiderPlugin.API.UninstallGame(Game.Id));')
assert s.count('UninstallGame') == 2
save(p, s)
print('BiS patch applied')
