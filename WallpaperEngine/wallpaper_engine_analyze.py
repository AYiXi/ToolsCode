import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed


class WallpaperEngineAnalyze:
    def __init__(self, pkg_dir: str, dst_dir: str, repkg_path: str):
        """
        :param pkg_dir: pkg dir like: SteamLibrary\steamapps\workshop\content\431960
        :param dst_dir: desitination wallpaper save dir : D:\Photo\WallpaperEngine
        :param repkg_path: D:\Download\RePKG.exe
        """
        self.pkg_dir = Path(pkg_dir)
        self.dst_dir = Path(dst_dir)
        self.temp_dir = Path(dst_dir) / 'temp'
        self.repkg_path = repkg_path
        self.command = '{repkg_path} extract -o {tmp_dir} -t -s {pkg_file}'

    def execute_command(self, pkg_file: str) -> Path:
        tmp_dir = self.temp_dir / Path(pkg_file).parent.name
        command = self.command.format(repkg_path=self.repkg_path, tmp_dir=tmp_dir, pkg_file=pkg_file)
        os.system(command)

        return tmp_dir

    def move_to_dst(self, tmp_dir: Path):
        jpg = tmp_dir.rglob('*.jpg')
        png = tmp_dir.rglob('*.png')

        img_path = list(jpg) or list(png)

        if img_path:
            img = max(img_path, key=lambda x: x.stat().st_size)
            suffix = '.jpg' if jpg else '.png'
            img.rename(self.dst_dir / (img.parent.name + suffix))

    def start(self):
        wallpaper_dir = self.pkg_dir
        pkg_files = wallpaper_dir.rglob('*.pkg')

        with ProcessPoolExecutor(max_workers=8) as exector:
            futures = [exector.submit(self.execute_command, pkg_file) for pkg_file in pkg_files]
            for future in as_completed(futures):
                if future.exception():
                    print(future.exception())

                self.move_to_dst(future.result())


if __name__ == '__main__':
    we = WallpaperEngineAnalyze(
            pkg_dir=r'D:\Games\SteamLibrary\steamapps\workshop\content\431960',
            dst_dir=r'D:\Photo\WallpaperEngine',
            repkg_path=r'D:\Soft\Repkg\RePKG.exe'
    )

    we.start()
